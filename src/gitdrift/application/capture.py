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
