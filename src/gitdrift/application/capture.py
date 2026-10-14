"""Repository-state capture use cases."""
from gitdrift.domain import RepositoryState, StateKind
from gitdrift.ports import (
    IgnoredPolicy,
    RepositoryReader,
    UntrackedPolicy,
)

def capture_head(reader: RepositoryReader) -> RepositoryState:
    """Capture immutable HEAD commit and tree identity through a repository port."""
    evidence = reader.capture_head()
    return RepositoryState(
        kind=StateKind.COMMIT,
        repository_id=evidence.repository_id,
        content_identity=f"commit:{evidence.commit_id};tree:{evidence.tree_id}",
        locators=(evidence.head_locator,) if evidence.head_locator else (),
    )

def capture_upstream(
    reader: RepositoryReader,
) -> RepositoryState | None:
    """Capture the configured upstream locator and immutable target."""
    evidence = reader.capture_upstream()
    if evidence is None:
        return None
    return RepositoryState(
        kind=StateKind.BRANCH_TIP,
        repository_id=evidence.repository_id,
        content_identity=(
            f"commit:{evidence.commit_id};tree:{evidence.tree_id}"
        ),
        locators=(evidence.locator,),
    )


def capture_index(reader: RepositoryReader) -> RepositoryState:
    """Capture a reproducible index manifest through a repository port."""
    evidence = reader.capture_index()
    base_state_id = None
    if evidence.base_commit_id and evidence.base_tree_id:
        base_state_id = RepositoryState(
            kind=StateKind.COMMIT,
            repository_id=evidence.repository_id,
            content_identity=(
                f"commit:{evidence.base_commit_id};tree:{evidence.base_tree_id}"
            ),
        ).id
    return RepositoryState(
        kind=StateKind.INDEX,
        repository_id=evidence.repository_id,
        content_identity=evidence.manifest_identity,
        base_state_id=base_state_id,
        limitations=evidence.limitations,
    )

def capture_working_tree(
    reader: RepositoryReader,
    *,
    untracked_policy: UntrackedPolicy = UntrackedPolicy.EXCLUDE,
    ignored_policy: IgnoredPolicy = IgnoredPolicy.EXCLUDE,
    selected_paths: tuple[str, ...] = (),
) -> RepositoryState:
    """Capture a reproducible working-tree manifest through a repository port."""
    evidence = reader.capture_working_tree(
        untracked_policy=untracked_policy,
        ignored_policy=ignored_policy,
        selected_paths=selected_paths,
    )
    base_state_id = RepositoryState(
        kind=StateKind.INDEX,
        repository_id=evidence.repository_id,
        content_identity=evidence.index_manifest_identity,
    ).id
    return RepositoryState(
        kind=StateKind.WORKING_TREE,
        repository_id=evidence.repository_id,
        content_identity=evidence.manifest_identity,
        base_state_id=base_state_id,
        limitations=evidence.limitations,
    )
