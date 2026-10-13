"""Repository-state capture use cases."""
from gitdrift.domain import RepositoryState, StateKind
from gitdrift.ports import RepositoryReader

def capture_head(reader: RepositoryReader) -> RepositoryState:
    """Capture immutable HEAD commit and tree identity through a repository port."""
    evidence = reader.capture_head()
    return RepositoryState(
        kind=StateKind.COMMIT,
        repository_id=evidence.repository_id,
        content_identity=f"commit:{evidence.commit_id};tree:{evidence.tree_id}",
        locators=(evidence.head_locator,) if evidence.head_locator else (),
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
